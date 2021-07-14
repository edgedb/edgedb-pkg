"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const process = __importStar(require("process"));
const slot_re = /^(?:(?:\w|-)+?)-(?<slot>\d+(?:-(?:alpha|beta|rc)\d+)?(?:-dev\d+)?).*\.(?:rpm|deb|img|pkg)$/gm;
const cv_re = /^(?:(?:\w|-)+?)-(?<slot>\d+(?:-(?:alpha|beta|rc)\d+)?(?:-dev\d+)?).*(?:\.cv(?<catver>\d+)).*\.(?:rpm|deb|img|pkg)$/gm;
async function run() {
    try {
        const target = process.env['INPUT_TARGET'];
        const path = process.env['INPUT_PATH'];
        const dest = `${path}/artifacts/${target}`;
        let version_slot = '';
        let catver = '';
        let found_file = '';
        let files = [];
        try {
            files = fs.readdirSync(dest);
        }
        catch (_a) {
        }
        console.log(`Looking for artifacts in ${dest}...`);
        for (let file of files) {
            let match = slot_re.exec(file);
            if (match !== null && match.groups !== undefined) {
                found_file = file;
                version_slot = match.groups.slot;
                match = cv_re.exec(file);
                if (match !== null && match.groups !== undefined) {
                    catver = match.groups.catver;
                }
                break;
            }
        }
        if (found_file !== '') {
            console.log(`File ${found_file} yields version slot '${version_slot}'`
                + ` and catalog version '${catver}'`);
        }
        console.log(`::set-output name=version-slot,::${version_slot}`);
        console.log(`::set-output name=catalog-version,::${catver}`);
    }
    catch (error) {
        console.log(`::error ${error.message}`);
        process.exit(1);
    }
}
run();
