import pandas as pd
import matplotlib.pyplot as plt
import pytz

def plot_metrics(csv_filename="metrics.csv", output_file=None):
    # Read the CSV data into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Convert the timestamp to a readable datetime format and set to UTC
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)

    # Convert to Beijing Time (UTC+8)
    beijing_tz = pytz.timezone('Asia/Shanghai')
    df['timestamp'] = df['timestamp'].dt.tz_convert(beijing_tz)

    # Create a 3x2 grid layout for the plots
    plt.figure(figsize=(14, 10))

    # Plot Memory usage (Used vs Free)
    plt.subplot(3, 2, 1)
    plt.plot(df['timestamp'], df['memory_used'], label='Memory Used (GiB)', color='blue')
    #plt.plot(df['timestamp'], df['memory_free'], label='Memory Free (GiB)', color='green')
    plt.title('Memory Usage')
    plt.xlabel('Time (Beijing Time)')
    plt.ylabel('Memory (GiB)')
    plt.legend()

    # Plot CPU Load (1 min, 5 min, 15 min averages)
    plt.subplot(3, 2, 2)
    plt.plot(df['timestamp'], df['load_avg_1min'], label='Load Average (1 min)', color='red')
    #plt.plot(df['timestamp'], df['load_avg_5min'], label='Load Average (5 min)', color='orange')
    #plt.plot(df['timestamp'], df['load_avg_15min'], label='Load Average (15 min)', color='yellow')
    plt.title('CPU Load Averages')
    plt.xlabel('Time (Beijing Time)')
    plt.ylabel('Load Average')
    plt.legend()

    # Plot Network Traffic (Packet send and receive)
    plt.subplot(3, 2, 3)
    plt.plot(df['timestamp'], df['packet_send'], label='Packet Sent (KiB/s)', color='purple')
    plt.plot(df['timestamp'], df['packet_receive'], label='Packet Received (KiB/s)', color='brown')
    plt.title('Network Traffic')
    plt.xlabel('Time (Beijing Time)')
    plt.ylabel('Traffic (KiB/s)')
    plt.legend()

    # Plot GPU Utilization (for GPU 0, 1, ..., 16 if available)
    plt.subplot(3, 2, 4)
    max_gpus = 16
    for i in range(max_gpus):
        # Plot GPU Utilization
        gpu_util_col = f'gpu_{i}_utilization_gpu'
        if gpu_util_col in df.columns:
            plt.plot(df['timestamp'], df[gpu_util_col], label=f'GPU {i} Utilization (%)')

    plt.title('GPU Utilization')
    plt.xlabel('Time (Beijing Time)')
    plt.ylabel('Utilization (%)')
    plt.legend()

    # Plot GPU Memory Usage (Used, Free, Total)
    plt.subplot(3, 2, 5)
    for i in range(max_gpus):
        gpu_memory_used_col = f'gpu_{i}_memory_used'
        gpu_memory_free_col = f'gpu_{i}_memory_free'
        gpu_memory_total_col = f'gpu_{i}_memory_total'

        if gpu_memory_used_col in df.columns and gpu_memory_free_col in df.columns and gpu_memory_total_col in df.columns:
            plt.plot(df['timestamp'], df[gpu_memory_used_col], label=f'GPU {i} Memory Used (MiB)', linestyle='--')
            #plt.plot(df['timestamp'], df[gpu_memory_free_col], label=f'GPU {i} Memory Free (MiB)', linestyle='-.')
            plt.plot(df['timestamp'], df[gpu_memory_total_col], label=f'GPU {i} Memory Total (MiB)', linestyle=':')

    plt.title('GPU Memory Usage')
    plt.xlabel('Time (Beijing Time)')
    plt.ylabel('Memory (MiB)')
    plt.legend()

    # Plot Disk Usage (Used vs Free)
    plt.subplot(3, 2, 6)
    plt.plot(df['timestamp'], df['storage_used'], label='Disk Used (GiB)', color='orange')
    #plt.plot(df['timestamp'], df['storage_free'], label='Disk Free (GiB)', color='green')
    plt.title('Disk Usage')
    plt.xlabel('Time (Beijing Time)')
    plt.ylabel('Disk (GiB)')
    plt.legend()

    # Adjust layout to prevent overlap
    plt.tight_layout()
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()