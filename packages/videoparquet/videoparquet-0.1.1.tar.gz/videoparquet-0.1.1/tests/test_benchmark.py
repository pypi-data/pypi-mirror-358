import pandas as pd
import numpy as np
import tempfile
import os
import time
import subprocess
from videoparquet.parquet2video import parquet2video
from videoparquet.video2parquet import video2parquet
import pytest
import shutil

def test_parquet_video_benchmark():
    # Generate synthetic data as uint8 to match video output
    num_frames, height, width, channels = 16, 64, 64, 3
    shape = (num_frames, height, width, channels)
    arr = (np.random.rand(*shape) * 255).astype(np.uint8)
    flat = arr.reshape(num_frames, -1)
    columns = [f'col{i}' for i in range(flat.shape[1])]
    df = pd.DataFrame(flat, columns=columns)
    minmax = [arr.min(), arr.max()]

    # Use a fixed output directory for inspection
    outdir = 'local_benchmark_output'
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir, exist_ok=True)

    parquet_path = os.path.join(outdir, 'data.parquet')
    df.to_parquet(parquet_path)
    parquet_size = os.stat(parquet_path).st_size / 2**20  # MB
    print(f'Parquet file size: {parquet_size:.2f} MB')

    # Conversion rule: only lossless codec
    conversion_rules = {
        'arr_lossless': (columns, shape, 0, {'c:v': 'ffv1'}, 8, minmax)
    }
    # Parquet -> Video
    t0 = time.time()
    results = parquet2video(parquet_path, 'benchid', conversion_rules, compute_stats=True, output_path=outdir, save_dataset=False)
    t1 = time.time()
    print(f'Parquet -> Video total time: {t1-t0:.2f}s')
    for name, stats in results.items():
        print(f"Video '{name}': Compressed size = {stats['compressed_size_MB']:.2f} MB, "
              f"Compression ratio = {stats['compression_ratio']:.2f}, "
              f"bpppb = {stats['bpppb']:.4f}, Write time = {stats['write_time_s']:.2f}s")
        # ffprobe pixel format
        video_path = os.path.join(outdir, 'benchid', f'{name}.mkv')
        try:
            pix_fmt = subprocess.check_output([
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=pix_fmt',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]).decode().strip()
        except Exception as e:
            pix_fmt = 'unknown'
        print(f"ffprobe pixel format for {name}: {pix_fmt}")
    # Video -> Parquet (restore)
    for name in conversion_rules.keys():
        t0 = time.time()
        recon_path = video2parquet(outdir, 'benchid', name=name)
        t1 = time.time()
        print(f'Video -> Parquet total time: {t1-t0:.2f}s')
        df_recon = pd.read_parquet(f'{outdir}/benchid/reconstructed_{name}.parquet')
        # Always print comparison summary
        diff = df.values - df_recon.values
        max_abs_err = np.max(np.abs(diff))
        mean_abs_err = np.mean(np.abs(diff))
        print('Original DataFrame head:')
        print(df.head())
        print('Restored DataFrame head:')
        print(df_recon.head())
        print(f'Max absolute error: {max_abs_err}')
        print(f'Mean absolute error: {mean_abs_err}')
        print('Example differences (first 5):')
        print(diff.flatten()[:5])
        if not np.allclose(df.values, df_recon.values, atol=1):
            print('WARNING: Restored DataFrame does not match original!')
        else:
            print('Restored DataFrame matches original (within atol=1).')
        video_size = os.stat(os.path.join(outdir, 'benchid', f'{name}.mkv')).st_size / 2**20
        print(f'Video file size: {video_size:.2f} MB')
        assert video_size < parquet_size, 'Video file is not smaller than original Parquet!' 