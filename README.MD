# Blockchain Reputation System using On-Chain Data

Español: [README.ES.md](README.ES.md)

This repository contains the source code for the Diploma Thesis: "Blockchain Reputation System using On-Chain Data," presented at the Faculty of Mathematics and Computation, University of Havana.

- **Author**: José Miguel Zayas Pérez
- **Advisors**: Lic. Ariel Díaz Pérez, Dr. Miguel Katrib Mora

🔗 **Project Link**: [https://github.com/josem-nex/blockchain-reputation](https://github.com/josem-nex/blockchain-reputation)

🔗 **Thesis PDF (spanish)**: [PDF](reputation.pdf)

---

## Project Summary

This project tackles the challenge of quantifying trust on the Blockchain. A data provider has been developed that processes the transactional history of a wallet on EVM networks to extract objective behavioral metrics. The solution uses a smart contract as an on-chain cache layer to drastically optimize performance. Its utility is demonstrated with a prototype system for P2P markets that translates these metrics into an intuitive trust score.

**Keywords**: Reputation System, Blockchain, On-chain, Smart Contract, Decentralized Trust.

## Key Features

- 🔍 **On-Chain Data Provider**: Analyzes a wallet's history to generate quantitative metrics about its activity.
- ⚡ **Smart Contract Cache**: Optimizes subsequent analyses using a smart contract and ensures data persistence with public access.
- 📊 **Reputation Model (P2P)**: Includes a use case that assigns a trust score in a P2P market.
- ⚙️ **RESTful API and Web UI**: Exposes functionality through an API (FastAPI) for integration and a web interface (Streamlit) for demos.

## Applications:

- **P2P Markets**: Increase trust among users.
- **DAOs**: Member evaluation, voting, and governance.
- **AIRDROPS**: Selection of trustworthy users.
- **JOBS**: Candidate evaluation, demonstration of on-chain experience.

## Tech Stack

- **Backend**: Python, FastAPI
- **Blockchain**: Solidity, Hardhat
- **Blockchain Interaction**: Web3.py
- **Demo Interface**: Streamlit
- **Testing Environment**: Ganache

## Installation and Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/josem-nex/blockchain-reputation.git
    cd blockchain-reputation
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the environment:**

    - Rename `.env.example` to `.env` and fill in the required values (RPC node URL, contract address, etc.).

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## Usage

The application can be operated in two ways:

1.  **Web Interface**: Navigate to the localhost address provided by Streamlit to perform manual analyses.
2.  **RESTful API**: Integrate the service into your applications by consuming the `/analyze` endpoint available at the link provided by the API upon startup.
