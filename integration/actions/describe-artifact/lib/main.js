"use strict";
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (Object.hasOwnProperty.call(mod, k)) result[k] = mod[k];
    result["default"] = mod;
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const process = __importStar(require("process"));
const re = /^(?:\w+)-(\d+(-(dev|alpha|beta|rc)\d+)?).*\.(rpm|deb|img)$/gm;
async function run() {
    try {
        const target = process.env['INPUT_TARGET'];
        const path = process.env['INPUT_PATH'];
        const dest = `${path}/artifacts/${target}`;
        let version_slot = '';
        let files = [];
        try {
            files = fs.readdirSync(dest);
        }
        catch (_a) {
        }
        console.log(`Looking for artifacts in ${dest}...`);
        for (let file of files) {
            let match = re.exec(file);
            if (match !== null) {
                version_slot = match[1];
            }
        }
        console.log(`::set-output name=version-slot,::${version_slot}`);
    }
    catch (error) {
        console.log(`::error ${error.message}`);
        process.exit(1);
    }
}
run();
