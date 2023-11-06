class Worker:
    def __init__(self, client, session):
        self.client = client
        self.session = session

    async def start(self):
        while True:
            data = await self.client.que.get()

            if data is None:
                await self.client.que.put(None)
                break

            parsed_data = await self.client.parser.process_data(self.session, data)
            await self.client.save(parsed_data)
            
            self.client.processed_urls += 1
            if self.client.debug:
                print(f"\033[33mTotally urls processed: {self.client.processed_urls}\033[0m")