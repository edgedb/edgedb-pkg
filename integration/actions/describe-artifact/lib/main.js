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
const glob = __importStar(require("glob"));
const tar = __importStar(require("tar-stream"));
const actions = __importStar(require("@actions/core"));
async function extractMetadata(tarball) {
    const readStream = fs.createReadStream(tarball);
    const extractor = tar.extract();
    const chunks = [];
    const promise = new Promise((resolve, reject) => {
        extractor.on('entry', function (header, stream, next) {
            if (header.name === 'build-metadata.json') {
                stream.on('data', chunk => {
                    chunks.push(chunk);
                });
            }
            stream.on('end', function () {
                next();
            });
            stream.resume();
        });
        extractor.on('finish', function () {
            if (chunks.length === 0) {
                reject(Error(`'build-metadata.json' not found in '${tarball}'`));
            }
            else {
                resolve(Buffer.concat(chunks).toString('utf-8'));
            }
        });
        readStream.pipe(extractor);
    });
    return await promise;
}
async function run() {
    var _a, _b, _c;
    try {
        const target = actions.getInput('target', { required: true });
        const path = actions.getInput('path', { required: true });
        const dest = `${path}/artifacts/${target}`;
        const tars = glob.sync('*.tar', { cwd: dest });
        if (tars.length === 0) {
            throw new Error(`no .tar artifacts found in ${dest}`);
        }
        else if (tars.length > 1) {
            throw new Error(`multiple .tar artifacts found in ${dest}`);
        }
        const tarball = `${dest}/${tars[0]}`;
        const metadata = JSON.parse(await extractMetadata(tarball));
        const version_slot = (_a = metadata['version_slot']) !== null && _a !== void 0 ? _a : '';
        const catver = (_b = metadata['version_details']['metadata']['catalog_version']) !== null && _b !== void 0 ? _b : '';
        const installref = (_c = metadata['installrefs'][0]) !== null && _c !== void 0 ? _c : '';
        actions.setOutput('version-slot', version_slot);
        actions.setOutput('catalog-version', catver);
        actions.setOutput('install-ref', installref);
    }
    catch (error) {
        actions.setFailed(error);
        process.exit(1);
    }
}
run();
