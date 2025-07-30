import os
import platform
import socket
import psutil
import netifaces
import cpuinfo
import pynvml
import time
import csv


def collect_metrics():
    kb = float(1024)
    mb = float(kb ** 2)
    gb = float(kb ** 3)

    memTotal = int(psutil.virtual_memory()[0] / gb)
    memFree = int(psutil.virtual_memory()[1] / gb)
    memUsed = int(psutil.virtual_memory()[3] / gb)
    memPercent = int(memUsed / memTotal * 100)
    storageTotal = int(psutil.disk_usage('/')[0] / gb)
    storageUsed = int(psutil.disk_usage('/')[1] / gb)
    storageFree = int(psutil.disk_usage('/')[2] / gb)
    storagePercent = int(storageUsed / storageTotal * 100)
    info = cpuinfo.get_cpu_info()['brand_raw']
    pidTotal = len(psutil.pids())
    load_avg_1 = round(os.getloadavg()[0], 2)
    load_avg_5 = round(os.getloadavg()[1], 2)
    load_avg_15 = round(os.getloadavg()[2], 2)
    core = os.cpu_count()
    host = socket.gethostname()
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    NVML_TEMPERATURE_GPU = 0
    gpu_info = []
    for device_index in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
        memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilizationRates = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_info.extend([
            memoryInfo.total / mb,
            memoryInfo.used / mb,
            memoryInfo.free / mb,
            utilizationRates.gpu,
            utilizationRates.memory,
            pynvml.nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        ])
    active = netifaces.gateways()['default'][netifaces.AF_INET][1]
    speed = psutil.net_io_counters(pernic=False)
    psend = round(speed[2] / kb, 2)
    precv = round(speed[3] / kb, 2)

    metrics = [
        time.time(),
        pidTotal,
        host,
        platform.system(),
        platform.machine(),
        platform.release(),
        platform.python_compiler(),
        info,
        core,
        memTotal,
        memFree,
        memUsed,
        memPercent,
        storageTotal,
        storageUsed,
        storageFree,
        storagePercent,
        load_avg_1,
        load_avg_5,
        load_avg_15,
        active,
        psend,
        precv
    ]
    metrics.extend(gpu_info)
    return metrics


def print_metrics(metrics):
    print()
    print(f"Running process: {metrics[1]}")

    print()
    print('---------- System Info ----------')
    print()
    print(f"Hostname     : {metrics[2]}")
    print(f"System       : {metrics[3]} {metrics[4]}")
    print(f"Kernel       : {metrics[5]}")
    print(f'Compiler     : {metrics[6]}')
    print(f'CPU          : {metrics[7]} {metrics[8]} (Core)')
    print(f"Memory       : {metrics[9]} GiB")
    print(f"Disk         : {metrics[13]} GiB")

    print()
    print('---------- Load Average ----------')
    print()
    print(f"Load avg (1 mins)  : {metrics[17]}")
    print(f"Load avg (5 mins)  : {metrics[18]}")
    print(f"Load avg (15 mins) : {metrics[19]}")

    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    if device_count > 0:
        print()
        print('---------- GPU ----------')
        for i in range(device_count):
            start_index = 23 + i * 6
            print(f"Device {i}")
            print(f"memory.total       : {metrics[start_index]} MiB")
            print(f"memory.used        : {metrics[start_index + 1]} MiB")
            print(f"memory.free        : {metrics[start_index + 2]} MiB")
            print(f"utilization.gpu    : {metrics[start_index + 3]}")
            print(f"utilization.memory : {metrics[start_index + 4]}")
            print(f"temperature.gpu    : {metrics[start_index + 5]} C")

    print()
    print('---------- RAM & Disk usage ----------')
    print()
    print(f"RAM Used         :  {metrics[11]} GiB / {metrics[9]} GiB ({metrics[12]} %)")
    print(f"Disk Used        :  {metrics[14]} GiB / {metrics[13]} GiB ({metrics[15]} %)")

    print()
    print('---------- Network stat ----------')
    print()
    print(f"Active interface :  {metrics[20]}")
    print(f"Packet send      :  {metrics[21]} KiB/s")
    print(f"Packet receive   :  {metrics[22]} KiB/s")


def collect_with_duration(duration=60*10, csv_filename="./llm_benchmark/metrics.csv", print_metrics=False):
    headers = [
        'timestamp',
        'running_processes',
        'hostname',
        'system',
        'machine',
        'kernel',
        'compiler',
        'cpu_info',
        'cpu_cores',
        'memory_total',
        'memory_free',
        'memory_used',
        'memory_percent',
        'storage_total',
        'storage_used',
        'storage_free',
        'storage_percent',
        'load_avg_1min',
        'load_avg_5min',
        'load_avg_15min',
        'active_interface',
        'packet_send',
        'packet_receive'
    ]
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    for device_index in range(device_count):
        headers.extend([
            f'gpu_{device_index}_memory_total',
            f'gpu_{device_index}_memory_used',
            f'gpu_{device_index}_memory_free',
            f'gpu_{device_index}_utilization_gpu',
            f'gpu_{device_index}_utilization_memory',
            f'gpu_{device_index}_temperature_gpu'
        ])

    with open(csv_filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        end_time = time.time() + duration
        while time.time() < end_time:
            metrics = collect_metrics()
            writer.writerow(metrics)
            if print_metrics:
                print_metrics(metrics)
            time.sleep(1)
