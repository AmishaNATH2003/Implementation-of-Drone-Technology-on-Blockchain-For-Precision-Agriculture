const CropWeedDetection = artifacts.require("CropWeedDetection.sol");

module.exports = function (deployer) {
  deployer.deploy(CropWeedDetection);
};
