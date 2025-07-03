# Helper Scripts (For Development Environments)

These scripts are located in the `scripts/` folder and are designed to help set up and test the environment on a local blockchain like Hardhat or Ganache.

## `scripts/deploy_contract.py`

Deploys the `WalletDataCache` smart contract to the blockchain. This is necessary so the main application can store and read the analysis results.

### Usage:

1.  Open the file and configure the connection parameters (`RPC_URL`, `DEPLOYER_ACCOUNT_INDEX`).
2.  Run the script from your terminal:

```bash
    python scripts/deploy_contract.py
```

The script will output the address of the new contract. Copy this address and paste it into the configuration parameters when running the app. The address is also saved to a generated .txt file.

## scripts/generate_transactions.py

Creates a large number of random ETH transactions between the available accounts on your node.

### Usage:

1. Open the file and adjust the parameters to fit your needs (TOTAL_TRANSACTIONS, ACCOUNTS_TO_USE, etc.).
2. Make sure your local node is running.
3. Run the script from your terminal:

```bash
    python scripts/generate_transactions.py
```
