const CropWeedDetection = artifacts.require("CropWeedDetection");

contract("CropWeedDetection", (accounts) => {
  let instance;

  const owner = accounts[0];
  const nonOwner = accounts[1];
  const sampleOperation = {
    ipfsHash: "QmSampleHash",
    areaCovered: 1000,
    pesticideAmount: 20,
    weedDetected: true,
    fieldID: 101,
  };

  beforeEach(async () => {
    // Deploy a fresh contract instance before each test
    instance = await CropWeedDetection.new({ from: owner });
  });

  it("should record a new operation successfully", async () => {
    const tx = await instance.recordOperation(
      sampleOperation.ipfsHash,
      sampleOperation.areaCovered,
      sampleOperation.pesticideAmount,
      sampleOperation.weedDetected,
      sampleOperation.fieldID,
      { from: owner }
    );

    // Verify the event
    assert.equal(tx.logs[0].event, "OperationRecorded", "OperationRecorded event should be emitted");
    assert.equal(tx.logs[0].args.operationID.toNumber(), 1, "Operation ID should be 1");

    // Verify the operation details
    const operation = await instance.getOperation(1);
    assert.equal(operation.ipfsHash, sampleOperation.ipfsHash, "IPFS hash should match");
    assert.equal(operation.areaCovered.toNumber(), sampleOperation.areaCovered, "Area covered should match");
    assert.equal(operation.pesticideAmount.toNumber(), sampleOperation.pesticideAmount, "Pesticide amount should match");
    assert.equal(operation.weedDetected, sampleOperation.weedDetected, "Weed detection status should match");
    assert.equal(operation.owner, owner, "Owner address should match");
    assert.equal(operation.fieldID.toNumber(), sampleOperation.fieldID, "Field ID should match");
  });

  it("should retrieve operations associated with the owner", async () => {
    await instance.recordOperation(
      sampleOperation.ipfsHash,
      sampleOperation.areaCovered,
      sampleOperation.pesticideAmount,
      sampleOperation.weedDetected,
      sampleOperation.fieldID,
      { from: owner }
    );

    const ownerOperations = await instance.getOwnerOperations({ from: owner });
    assert.equal(ownerOperations.length, 1, "Owner should have one operation");
    assert.equal(ownerOperations[0].toNumber(), 1, "Operation ID should be 1");
  });

  it("should only allow the owner to call sprayPesticide", async () => {
    await instance.recordOperation(
      sampleOperation.ipfsHash,
      sampleOperation.areaCovered,
      sampleOperation.pesticideAmount,
      sampleOperation.weedDetected,
      sampleOperation.fieldID,
      { from: owner }
    );

    // Success case: owner calls sprayPesticide
    await instance.sprayPesticide(1, { from: owner });

    // Failure case: non-owner tries to call sprayPesticide
    try {
      await instance.sprayPesticide(1, { from: nonOwner });
      assert.fail("Non-owner should not be able to call sprayPesticide");
    } catch (err) {
      assert.include(err.message, "You are not the owner of this operation", "Expected error not thrown");
    }
  });

  it("should fail to spray pesticide if weeds are not detected", async () => {
    await instance.recordOperation(
      sampleOperation.ipfsHash,
      sampleOperation.areaCovered,
      sampleOperation.pesticideAmount,
      false, // No weeds detected
      sampleOperation.fieldID,
      { from: owner }
    );

    try {
      await instance.sprayPesticide(1, { from: owner });
      assert.fail("Spraying should fail if no weeds are detected");
    } catch (err) {
      assert.include(err.message, "No weeds detected for this operation", "Expected error not thrown");
    }
  });
});
