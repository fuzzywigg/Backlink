import time
import json
import random
from proxy_agent import TheProxy

# NIGHT STRATEGY: "Paper Clipper"
# Monitors a "dummy" price feed and generates Iron Dome proposals 
# to test the pipeline stability overnight.

class PaperTrader:
    def __init__(self):
        self.agent = TheProxy()
        # Mock strategy: Buy ETH if price "dips" (randomly simulated for test)
        self.last_price = 3000.0 
        
    def run_night_shift(self, duration_hours=8):
        print(f"🌙 NIGHT SHIFT: Starting Paper Trader for {duration_hours} hours...")
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        cycles = 0
        
        while time.time() < end_time:
            cycles += 1
            print(f"\n[CYCLE {cycles}] {time.ctime()}")
            
            # 1. Scout Info (Mocking price fluctuation since we don't want to spam a real site all night)
            # In real prod, self.agent.fetch_price(...)
            
            # Simulate price walk
            movement = random.uniform(-50, 50)
            current_price = self.last_price + movement
            print(f"   📈 Simulated ETH Price: ${current_price:.2f}")
            
            # 2. Strategy Logic
            if current_price < self.last_price - 20:
                print("   💡 STRATEGY SIGNAL: DIP DETECTED! BUY!")
                
                # 3. Execution (The Iron Dome Link)
                # We propose a trade of 0.1 ETH for USDT
                self.agent.propose_trade(
                    chain="ethereum",
                    from_addr="0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8", # Compromised/Burned address (Safe for test)
                    to_addr="0xdAC17F958D2ee523a2206206994597C13D831ec7", # USDT
                    amount=0.1,
                    data="BUY_ETH_SIMULATION"
                )
                
            elif current_price > self.last_price + 20:
                print("   💡 STRATEGY SIGNAL: PUMP DETECTED! SELL!")
                # Propose Sell
                self.agent.propose_trade(
                    chain="ethereum",
                    from_addr="0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8",
                    to_addr="0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    amount=0.0, # 0 ETH value, just data
                    data="SELL_ETH_SIMULATION"
                )
            else:
                print("   💤 Market Chop. Holding.")

            self.last_price = current_price
            
            # Sleep 10 minutes to simulate realistic low-freq trading
            # For demo immediate feedback, we sleep 1 minute
            time.sleep(60) 

        print("☀️ NIGHT SHIFT COMPLETE.")

if __name__ == "__main__":
    bot = PaperTrader()
    bot.run_night_shift(duration_hours=8)
