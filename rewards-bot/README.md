# Rewards Distribution Bot

A Python script for automating token distribution on a Dymension blockchain network. This bot helps in sending rewards to multiple addresses while tracking processed transactions to prevent duplicate sends.

## Features

- Reads reward data from JSON files
- Supports multiple input formats (list of addresses or structured data with amounts)
- Tracks processed transactions to prevent double-sending
- Handles errors gracefully with detailed logging
- Stores transaction hashes for successful transfers

## Prerequisites

- Python 3.x
- Access to a Dymension node
- The Dymension binary (`dymd`) installed
- A funded wallet with proper permissions to send tokens

## Input File Format

The script accepts JSON files in the following formats:

### Rewards Data Format

```json
[
    {
        "dym_address": "dym1...",
        // amount of rewards to send in adym
        "rewards": 1000000000000000000
    }
]
```

## Usage

1. Run the script:

```bash
python rewards-bot.py
```

2. You will be prompted to enter:
   - Binary path (path to your `dymd` executable)
   - Key name (your wallet name)
   - Keyring (usually "test" or "file")
   - Chain ID (e.g., "froopyland_100-1")
   - RPC URL (e.g., "http://localhost:26657")
   - Path to the rewards data file
   - Path to the results file (for tracking processed transactions)

## Output

The script creates a results file that tracks:
- Processed addresses
- Transaction hashes for successful transfers

The results file format:
```json
[
    {
        "address": "dym1...",
        "tx_hash": "ABCD..."
    }
]
```

## Error Handling

The script includes comprehensive error handling for:
- File not found errors
- JSON parsing errors
- Transaction execution errors
- Invalid data formats

## Security Considerations

- Always verify the rewards data file before processing
- Keep your keyring credentials secure
- Double-check the RPC endpoint
- Test with small amounts first

## Transaction Details

- Gas adjustment: 1.4
- Gas prices: 20000000000adym
- Gas estimation: automatic
- 8-second delay between transactions
- Amounts are converted from DYM to adym (×10¹⁸)

## Example Command Flow

```bash
$ python rewards-bot.py
Enter the binary path: /usr/local/bin/dymd
Enter the key name: mykey
Enter the keyring: test
Enter the chain ID: froopyland_100-1
Enter the RPC URL: http://localhost:26657
Enter the files to send rewards from: rewards.json
Enter the results file: processed_transactions.json
```

## Notes

- Failed transactions will not be marked as processed
- The script can be safely interrupted and restarted, as it tracks processed addresses
- Progress is displayed as "X/Y transactions processed"
