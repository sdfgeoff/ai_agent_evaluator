set -x

# Build the in-container agent
cd simple-agent && cargo build --target x86_64-unknown-linux-musl  && cd ../

# Run the scaffold
cd scaffold/src && uv run -m scaffold \
    --agent-binary ../../simple-agent/target/x86_64-unknown-linux-musl/debug/simple-agent \
    --input-directory ../../inputs \
    --output-directory ../../outputs \

# cd evaluator/packages/scaffold/src && uv sync && uv run -m scaffold 