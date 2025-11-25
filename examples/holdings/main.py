from dotenv import load_dotenv
from jup_python_sdk.clients.ultra_api_client import UltraApiClient

load_dotenv()
client = UltraApiClient()

address = client._get_public_key()

try:
    holdings_response = client.holdings(str(address))

    print("Holdings API Response:")
    print(f"Total Portfolio Value: {holdings_response['uiAmount']} ({holdings_response['uiAmountString']})")
    
    print("\nToken Holdings:")
    for mint, token_accounts in holdings_response['tokens'].items():
        print(f"\nToken Mint: {mint}")
        for account in token_accounts:
            print(f"  Account: {account['account']}")
            print(f"  Amount: {account['uiAmountString']}")
            print(f"  Decimals: {account['decimals']}")
            print(f"  Is ATA: {account['isAssociatedTokenAccount']}")
            print(f"  Is Frozen: {account['isFrozen']}")
            print(f"  Exclude From Net Worth: {account['excludeFromNetWorth']}")

except Exception as e:
    print("Error occurred while fetching holdings:", str(e))
finally:
    client.close()