import speedtest
import time
import os
import tempfile
try:
    import pynvml
except ImportError:
    print("Warning: pynvml not available, GPU monitoring features disabled")
import numpy as np
from numba import cuda

class ManagerSpeed:
    results = {}
    @classmethod
    def network(cls):
        """Test network speed"""
        try:
            st = speedtest.Speedtest(secure=True, source_address=None)
            st.get_best_server()

            download_speed = st.download() / 1_000_000
            upload_speed = st.upload() / 1_000_000
            ping = st.results.ping

            cls.results["network"] = {
                "download_speed": f"{download_speed:.2f} Mbps",
                "upload_speed": f"{upload_speed:.2f} Mbps",
                "ping": f"{ping:.2f} ms",
            }
            info = f"""\n network test result:
download speed: {cls.results['network']['download_speed']}
upload speed: {cls.results['network']['upload_speed']}
ping: {cls.results['network']['ping']}
"""

            print(info)
            return info

        except Exception as e:
            print(f"network test failed: {str(e)}")
            cls.results["network"] = None
            return f"network test failed: {str(e)}"

    @classmethod
    def disk(cls, file_size_mb=100):
        """Test disk read and write speed"""
        try:
            # Create a temporary test file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_path = temp_file.name

            # Write test
            data = os.urandom(1024 * 1024)  # 1MB random data
            start_time = time.time()

            for _ in range(file_size_mb):
                temp_file.write(data)
            temp_file.close()

            write_time = time.time() - start_time
            write_speed = file_size_mb / write_time  # MB/s

            # Read test
            start_time = time.time()
            with open(file_path, "rb") as f:
                while f.read(1024 * 1024):

                    pass

            read_time = time.time() - start_time
            read_speed = file_size_mb / read_time  # MB/s

            # Clean up the temporary file
            os.unlink(file_path)

            cls.results["disk"] = {
                "read_speed": f"{read_speed:.2f} MB/s",
                "write_speed": f"{write_speed:.2f} MB/s",
            }
            info = f"""\n disk test result:
read speed: {cls.results['disk']['read_speed']}
write speed: {cls.results['disk']['write_speed']}
"""

            print(info)
            return info

        except Exception as e:
            print(f"disk test failed: {str(e)}")
            cls.results["disk"] = None
            return f"disk test failed: {str(e)}"

    @classmethod
    def memory(cls, size_mb=1000):
        """Test memory read and write speed"""
        try:
            num_elements = (
                size_mb * 1024 * 1024 // 8
            )  # Calculate the number of double precision floating point numbers
            # Write test (includes the time for NumPy to generate data efficiently)
            start_time = time.time()
            data = np.random.rand(num_elements)

            write_time = time.time() - start_time
            write_speed = size_mb / write_time

            # Read test (force reading data)
            start_time = time.time()
            _ = np.sum(data)  # Ensure data is read
            read_time = time.time() - start_time
            read_speed = size_mb / read_time

            # Store results...
            info = f"""\n memory test result:
read speed: {read_speed:.2f} MB/s
write speed: {write_speed:.2f} MB/s"""

            print(info)
            return info

        except Exception as e:
            return f"memory test failed: {str(e)}"

    @classmethod
    def gpu_memory(cls):
        """Test GPU memory usage"""
        try:
            pynvml.nvmlInit()
            deviceCount = pynvml.nvmlDeviceGetCount()
            gpu_results = []

            for i in range(deviceCount):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                size_bytes = 1000 * 1024 * 1024

                # Generate random data
                host_data = np.random.rand(size_bytes // 4).astype(np.float32)

                # Write test: Host to Device
                start_time = time.time()
                device_data = cuda.to_device(host_data)
                write_time = time.time() - start_time
                write_speed = 1000 / write_time

                # Read memory test
                start_time = time.time()
                device_data.copy_to_host()
                read_time = time.time() - start_time
                read_speed = 1000 / read_time

                gpu_info = {
                    "name": name,
                    "total_memory": f"{memory.total / (1024**2):.2f} MB",
                    "used_memory": f"{memory.used / (1024**2):.2f} MB",
                    "free_memory": f"{memory.free / (1024**2):.2f} MB",
                    "gpu_utilization": f"{utilization.gpu}%",
                    "memory_utilization": f"{utilization.memory}%",
                    "write_speed": f"{write_speed:.2f} MB/s",
                    "read_speed": f"{read_speed:.2f} MB/s",
                }
                gpu_results.append(gpu_info)

            cls.results["gpu"] = gpu_results
            pynvml.nvmlShutdown()
            info = f"""\nGPU test result:"""
            for i, gpu in enumerate(cls.results["gpu"]):
                info += f"""\nGPU {i+1}:
name: {gpu['name']}
total memory: {gpu['total_memory']}
used memory: {gpu['used_memory']}
free memory: {gpu['free_memory']}
gpu utilization: {gpu['gpu_utilization']}
memory utilization: {gpu['memory_utilization']}
write speed: {gpu['write_speed']}
read speed: {gpu['read_speed']}"""
            print(info)
            return info
        except Exception as e:

            print(f"GPU test failed: {str(e)}")
            cls.results["gpu"] = None
            return f"GPU test failed: {str(e)}"
