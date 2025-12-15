import asyncio

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {}
        return cls._instance

    def subscribe(self, topic, func):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(func)
        print(f"📡 EventBus: New subscriber for topic '{topic}'")

    async def publish(self, topic, data):
        if topic in self.subscribers:
            print(f"📨 EventBus: Publishing to '{topic}' with payload size {len(str(data))}")
            tasks = []
            for func in self.subscribers[topic]:
                if asyncio.iscoroutinefunction(func):
                    tasks.append(asyncio.create_task(func(data)))
                else:
                    # Se não for async, executa direto (fallback)
                    func(data)

            if tasks:
                await asyncio.gather(*tasks)
        else:
            print(f"⚠️ EventBus: No subscribers for '{topic}'")
