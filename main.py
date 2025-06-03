import asyncio
import time

class DataProcessor:
    def __init__(self, data):
        self.data = data

    async def process_data(self):
        print("Processing started...")
        await asyncio.sleep(2)  # Simulating a time-consuming task
        print(f"Data processed: {self.data}")

    async def fast_process(self):
        print("Fast processing started...")
        await asyncio.sleep(0.5)  # Simulate a faster process
        print(f"Fast processed data: {self.data}")

# Function to run the data processing
async def run_processing():
    processor = DataProcessor("Sample data")
    await processor.process_data()
    await processor.fast_process()

# Entry point
if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(run_processing())
    print(f"Total execution time: {time.time() - start_time} seconds")
