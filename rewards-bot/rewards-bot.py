import json
import subprocess
import time

def read_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"Read data: {data}")
            
            if isinstance(data, list):
                # Handle list of strings (addresses)
                if all(isinstance(x, str) for x in data):
                    return set(data)
                # Handle list of dictionaries
                return {entry["dym_address"] for entry in data 
                       if isinstance(entry, dict) and "dym_address" in entry}
            elif isinstance(data, dict) and "dym_address" in data:
                return {data["dym_address"]}
            else:
                print(f"Warning: Unexpected data format in {file_path}")
                return set()
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return set()
    except Exception as e:
        print(f"Unexpected error reading {file_path}: {e}")
        return set()

def extract_txhash(stdout):
    """Extract transaction hash from the command output."""
    for line in stdout.split('\n'):
        if line.startswith('txhash:'):
            return line.split(':', 1)[1].strip()
    return None

def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def send_tokens(binary_path, key_name, address, amount, keyring, chain_id, rpc):
    try:
        command = [
            binary_path,
            "tx",
            "bank",
            "send",
            key_name,
            address,
            amount,
            "--keyring-backend", keyring,
            "--chain-id", chain_id,
            "--node", rpc,
             "--gas-adjustment", "1.4",
            "--gas", "auto",
            "--gas-prices","20000000000adym",
            "--yes" 
        ]
        print(f"Executing: {' '.join(command)}")

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            txhash = extract_txhash(result.stdout)
            return txhash
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def read_processed_addresses(file_path):
    """Read the processed addresses from the tracking file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"Read processed addresses: {data}")
            # Handle list of dictionaries with address and tx_hash
            if isinstance(data, list) and all(isinstance(x, dict) for x in data):
                return set(entry["address"] for entry in data)
            else:
                print(f"Warning: Unexpected format in processed addresses file {file_path}")
                return set()
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return set()
    except Exception as e:
        print(f"Unexpected error reading {file_path}: {e}")
        return set()

def read_rewards_data(file_path):
    """Read the rewards data file containing addresses and amounts."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"Read rewards data from {file_path}")
            if isinstance(data, list):
                return [entry for entry in data 
                        if isinstance(entry, dict) 
                        and "dym_address" in entry 
                        and "rewards" in entry]
            else:
                print(f"Warning: Unexpected data format in {file_path}")
                return []
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error reading {file_path}: {e}")
        return []

if __name__ == "__main__":

    binary_path = input("Enter the binary path: ").strip()
    key_name = input("Enter the key name: ").strip()
    keyring = input("Enter the keyring: ").strip()
    chain_id = input("Enter the chain ID: ").strip()
    rpc = input("Enter the RPC URL: ").strip()
    rewards_file = input("Enter the files to send rewards from: ").strip()
    results_file = input("Enter the results file: ").strip()

    processed_addresses = read_processed_addresses(results_file)

    rewards_data = read_rewards_data(rewards_file)
    total_tx = len(rewards_data)
    processed_count = 0
    processed_data_list = []
    try:
        # Try to read existing processed data
        with open(processed_file, "r", encoding="utf-8") as file:
            processed_data_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        processed_data_list = []

    print(f"Starting to process {total_tx} transactions...")

    for entry in rewards_data:
            address = entry["dym_address"]
            amount = f"{int(entry['rewards'] * 10**18)}adym"
                
            if address in processed_addresses:
                print(f"Skipping already processed address: {address}")
                processed_count += 1
                print(f"Progress: {processed_count}/{total_tx} transactions processed")
                continue
                
            result = send_tokens(binary_path, key_name, address, amount, keyring, chain_id, rpc)
            if result != None:
                processed_addresses.add(address)
                # Store both address and tx hash
                processed_data = {
                    "address": address,
                    "tx_hash": result
                }
                processed_data_list.append(processed_data)
                write_json(processed_file, processed_data_list)
                processed_count += 1
                print(f"Progress: {processed_count}/{total_tx} transactions processed")
                print("Sleeping for 8 seconds...")
                time.sleep(8)

    print(f"\nCompleted! {processed_count}/{total_tx} transactions processed successfully.")