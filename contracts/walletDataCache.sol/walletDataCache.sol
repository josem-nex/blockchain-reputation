// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; 

import "hardhat/console.sol";  // debug con console.log en Solidity

contract WalletDataCache {
    address public owner;

    struct WalletMetrics {
        uint256 txIn;
        uint256 txOut;
        uint256 totalTxs;
        uint256 failedTxs;
        uint256 gasUsed;
        uint256 feePaid; // En Wei
        uint256 contractsCreatedCount;
        uint256 distinctErc20Count;
        uint256 distinctNftCount;
        uint256 activeDaysCount;
        uint256 firstTxTimestamp;
    }

    mapping(address => WalletMetrics) public walletMetricsCache;
    mapping(address => uint256) public lastProcessedBlock;

    event WalletDataUpdated(address indexed wallet, uint256 lastBlock);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor() {
        owner = msg.sender;
        console.log("WalletDataCache deployed by:", msg.sender);
        emit OwnershipTransferred(address(0), owner);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "WalletDataCache: Caller is not the owner");
        _;
    }

    function updateWalletData(
        address _wallet,
        WalletMetrics calldata _metrics,
        uint256 _blockNumber
    ) external onlyOwner {
        walletMetricsCache[_wallet] = _metrics;
        lastProcessedBlock[_wallet] = _blockNumber;
        emit WalletDataUpdated(_wallet, _blockNumber);
    }

    function getWalletData(address _wallet)
        external
        view
        returns (WalletMetrics memory, uint256)
    {
        return (walletMetricsCache[_wallet], lastProcessedBlock[_wallet]);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "WalletDataCache: New owner is the zero address");
        owner = newOwner;
        emit OwnershipTransferred(msg.sender, newOwner);
    }
}