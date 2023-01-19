import curseforge from '@meza/curseforge-fingerprint';
import path from 'path';
import { argv, exit } from 'process';

// console.log(argv)

if (argv.length > 2) {
    let filePath = argv[2]
    const fingerprint = curseforge.fingerprint(filePath);
    console.log(fingerprint)
} else {
    exit(-1)
}
