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
async function run() {
    var _a, _b, _c;
    try {
        const target = process.env['INPUT_TARGET'];
        const path = process.env['INPUT_PATH'];
        const dest = `${path}/artifacts/${target}`;
        let metadata = JSON.parse(fs.readFileSync(`${dest}/package-version.json`, 'utf8'));
        let version_slot = (_a = metadata['version_slot']) !== null && _a !== void 0 ? _a : '';
        let catver = (_b = metadata['catalog_version']) !== null && _b !== void 0 ? _b : '';
        let installref = (_c = metadata['installref']) !== null && _c !== void 0 ? _c : '';
        console.log(`::set-output name=version-slot,::${version_slot}`);
        console.log(`::set-output name=catalog-version,::${catver}`);
        console.log(`::set-output name=install-ref,::${installref}`);
    }
    catch (error) {
        console.log(`::error ${error.message}`);
        process.exit(1);
    }
}
run();
