import * as fs from 'fs'
import * as process from 'process'
import * as glob from 'glob'
import * as tar from 'tar-stream'

import * as actions from '@actions/core'

async function extractMetadata(tarball: string): Promise<string> {
  const readStream = fs.createReadStream(tarball)
  const extractor = tar.extract()
  const chunks: Buffer[] = []

  const promise: Promise<string> = new Promise((resolve, reject) => {
    extractor.on('entry', function (header, stream, next) {
      if (header.name === 'build-metadata.json') {
        stream.on('data', chunk => {
          chunks.push(chunk)
        })
      }

      stream.on('end', function () {
        next() // ready for next entry
      })

      stream.resume() // just auto drain the stream
    })

    extractor.on('finish', function () {
      if (chunks.length === 0) {
        reject(Error(`'build-metadata.json' not found in '${tarball}'`))
      } else {
        resolve(Buffer.concat(chunks).toString('utf-8'))
      }
    })

    readStream.pipe(extractor)
  })

  return await promise
}

async function run(): Promise<void> {
  try {
    const target = actions.getInput('target', {required: true})
    const path = actions.getInput('path', {required: true})
    const dest = `${path}/artifacts/${target}`
    const tars = glob.sync('*.tar', {cwd: dest})
    if (tars.length === 0) {
      throw new Error(`no .tar artifacts found in ${dest}`)
    } else if (tars.length > 1) {
      throw new Error(`multiple .tar artifacts found in ${dest}`)
    }
    const tarball = `${dest}/${tars[0]}`

    const metadataJSON = await extractMetadata(tarball)
    const metadata = JSON.parse(metadataJSON)
    const version_slot = metadata['version_slot'] ?? ''
    const catver =
      metadata['version_details']['metadata']['catalog_version'] ?? ''
    const installref = metadata['installrefs'][0] ?? ''

    actions.setOutput('metadata', metadataJSON)
    actions.setOutput('version', metadata['version'])
    actions.setOutput('version-slot', version_slot)
    actions.setOutput('catalog-version', catver)
    actions.setOutput('install-ref', installref)
  } catch (error) {
    actions.setFailed(error as Error)
    process.exit(1)
  }
}

run()
