import * as process from 'process'
import * as cp from 'child_process'
import * as path from 'path'

// shows how the runner will run a javascript action with env / stdout protocol
test('test runs', () => {
    process.env['INPUT_TARGET'] = 'centos-7';
    process.env['INPUT_PATH'] = __dirname;
    const ip = path.join(__dirname, '..', 'lib', 'main.js');
    const options: cp.ExecSyncOptions = {
        env: process.env
    };
    let output = cp.execSync(`node ${ip}`, options).toString().trim();
    expect(output).toEqual(expect.stringContaining("::set-output name=version-slot,::1-alpha2"))
});

test('test runs', () => {
    process.env['INPUT_TARGET'] = 'ubuntu-xenial';
    process.env['INPUT_PATH'] = __dirname;
    const ip = path.join(__dirname, '..', 'lib', 'main.js');
    const options: cp.ExecSyncOptions = {
        env: process.env
    };
    let output = cp.execSync(`node ${ip}`, options).toString().trim();
    expect(output).toEqual(expect.stringContaining("::set-output name=version-slot,::1-alpha6-dev5057"))
});
