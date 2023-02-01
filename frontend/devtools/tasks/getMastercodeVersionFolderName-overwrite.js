/**
 * This file has been added to enable building the portal inside a container without a surrounding git repo.
 * The original file will be overwritten only inside the frontend_prod container (see Dockerfile.prod file)
 */
const path = require("path"),
    rootPath = path.resolve(__dirname, "../../"),
    stableVersionNumber = require(path.resolve(
        rootPath,
        "devtools/tasks/getStableVersionNumber"
    ))();

module.exports = function getMastercodeVersionFolderName() {
    return stableVersionNumber;
};

