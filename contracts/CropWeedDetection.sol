// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CropWeedDetection {

    struct Operation {
        string imageHash;           // IPFS hash of the segmented image
        uint256 areaCovered;        // Area covered by drone (in sq. meters)
        uint256 pesticideAmount;    // Amount of pesticide sprayed (in liters)
        bool weedDetected;          // Whether weeds were detected
        uint256 fieldId;            // Field ID assigned to the farmer
        address owner;              // Address of the field owner
        uint256 area;               // Total area of the field
        uint256 weedPercent;        // Percentage of weeds in the area
        uint256 dosePerSqM;         // Dose per square meter
        uint256 efficiencyFactor;   // Efficiency factor in percent
        uint256 totalPesticide;     // Total calculated pesticide
    }

    uint256 public operationCount;
    mapping(uint256 => Operation) public operations;
    mapping(address => uint256[]) private ownerToOperations;

    // Event triggered when a new operation is recorded
    event OperationRecorded(
        uint256 indexed operationId,
        string imageHash,
        uint256 areaCovered,
        uint256 pesticideAmount,
        bool weedDetected,
        uint256 fieldId,
        address indexed owner
    );

    // Event triggered to notify the drone system to spray pesticide
    event PesticideSprayTriggered(
        uint256 indexed operationId,
        address indexed owner,
        uint256 pesticideAmount
    );

    // Modifier to restrict access to the owner of a record
    modifier onlyOwner(uint256 operationId) {
        require(
            operations[operationId].owner == msg.sender,
            "Not authorized: You are not the owner."
        );
        _;
    }

    /// @notice Record a drone operation after image processing and detection
    function recordOperation(
        string memory imageHash,
        uint256 areaCovered,
        uint256 pesticideAmount,
        bool weedDetected,
        uint256 fieldId
    ) public {
        operationCount++;
        operations[operationCount] = Operation({
            imageHash: imageHash,
            areaCovered: areaCovered,
            pesticideAmount: pesticideAmount,
            weedDetected: weedDetected,
            fieldId: fieldId,
            owner: msg.sender,
            area: 0,
            weedPercent: 0,
            dosePerSqM: 0,
            efficiencyFactor: 0,
            totalPesticide: 0
        });

        ownerToOperations[msg.sender].push(operationCount);

        emit OperationRecorded(
            operationCount,
            imageHash,
            areaCovered,
            pesticideAmount,
            weedDetected,
            fieldId,
            msg.sender
        );
    }

    /// @notice Trigger pesticide spraying if weeds are detected
    function sprayPesticide(uint256 operationId) public onlyOwner(operationId) {
        Operation storage op = operations[operationId];
        require(op.weedDetected, "No weeds detected for this operation.");
        emit PesticideSprayTriggered(operationId, msg.sender, op.pesticideAmount);
    }

    /// @notice Get list of operation IDs owned by the sender
    function getMyOperations() public view returns (uint256[] memory) {
        return ownerToOperations[msg.sender];
    }

    /// @notice Get details of a specific operation
    function getOperationDetails(uint256 operationId)
        public
        view
        returns (
            string memory imageHash,
            uint256 areaCovered,
            uint256 pesticideAmount,
            bool weedDetected,
            uint256 fieldId,
            address owner
        )
    {
        Operation memory op = operations[operationId];
        return (
            op.imageHash,
            op.areaCovered,
            op.pesticideAmount,
            op.weedDetected,
            op.fieldId,
            op.owner
        );
    }

    /// @notice Calculate total pesticide required based on field parameters
    function calculatePesticideAmount(
        uint256 area,              // Area in m²
        uint256 weedPercent,       
        uint256 dosePerSqM,        
        uint256 efficiencyFactor   
    ) public pure returns (uint256) {
        require(weedPercent <= 100, "Invalid weed percent");
        require(efficiencyFactor <= 100, "Invalid efficiency factor");

        // Formula: T = A * (W% / 100) * P * (E / 100)
        uint256 weedArea = (area * weedPercent) / 100;
        uint256 adjustedDose = (dosePerSqM * efficiencyFactor) / 100;
        uint256 totalPesticide = weedArea * adjustedDose;

        return totalPesticide;
    }
}
