import { createChatGPT } from "../sdk/packages/local/dist/index.js";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { homedir } from "node:os";

const cryptoPath = fileURLToPath(
    new URL("./crypto.ps1", import.meta.url)
);

function protect(mode, data) {
    const result = spawnSync("powershell.exe", [
        "-NoProfile",
        "-NonInteractive",
        "-File",
        cryptoPath,
        mode
    ], {
        input: Buffer.from(data).toString("base64"),
        encoding: "utf8",
        windowsHide: true
    });

    if (result.error || result.status !== 0) {
        throw new Error("Windows encryption failed");
    }

    return Buffer.from(result.stdout.trim(), "base64");
}

const client = createChatGPT({
    appName: "GPT Terminal",
    appId: "gpt-terminal",
    redirectPort: 0,
    storageDir: join(
        process.env.LOCALAPPDATA || homedir(),
        "GPT-Terminal",
        "auth"
    ),

    credentialEncryption: {
        id: "windows-dpapi-v1",

        isAvailable() {
            return process.platform === "win32";
        },

        encrypt(plaintext) {
            return protect("encrypt", Buffer.from(plaintext));
        },

        decrypt(ciphertext) {
            return protect("decrypt", ciphertext).toString("utf8");
        }
    }
});

const command = process.argv[2];

try {
    let result;

    switch (command) {
        case "login":
            result = await client.signIn();
            break;

        case "status":
            result = await client.getSession();
            break;

        case "models":
            result = await client.listModels();
            break;

        case "logout":
            await client.disconnect();
            result = { status: "disconnected" };
            break;

        case "chat":
            const model = process.argv[3];
            const message = process.argv.slice(4).join(" ");

            result = await client.streamResponse({
                model,
                input: message
            });
            break;


        case "agent": {
            let raw = "";

            for await (const chunk of process.stdin) {
                raw += chunk.toString("utf8");
            }

            const request = JSON.parse(raw);

            result = await client.streamResponse({
                model: request.model,
                input: request.messages,
                instructions: request.instructions
            });

            break;
        }


        case "stream": {
            let raw = "";

            process.stdin.setEncoding("utf8");

            for await (const chunk of process.stdin) {
                raw += chunk;
            }

            const request = JSON.parse(raw);

            await client.streamResponse({
                model: request.model,
                input: request.messages,
                instructions: request.instructions,

                onDelta(delta) {
                    process.stdout.write(delta);
                }
            });

            break;
        }

        default:
            throw new Error("Unknown command");
    }

    if (command !== "stream") {
        console.log(JSON.stringify(result, null, 2));
    }

} catch (error) {
    console.error(JSON.stringify({
        error: error.code || "unknown",
        message: error.message
    }));

    process.exitCode = 1;
}
