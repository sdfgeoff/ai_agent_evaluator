set -e

# # Build the in-container agent
# cd simple-agent && cargo build --target x86_64-unknown-linux-musl  && cd ../

cd evaluator;

# Build the binary that will be copied into each of the docker containers
cargo build --target x86_64-unknown-linux-musl --bin simple-agent

# Run the scaffold
cargo run --bin scaffold -- \
    --agent-binary ../evaluator/target/x86_64-unknown-linux-musl/debug/simple-agent \
    --input-directory ../inputs \
    --output-directory ../outputs \
    --llm-providers-config ../llm_providers.json

cd ../;

# # Run the scaffold
cd scaffold/src && uv run -m scaffold \
    --output-directory ../../outputs \

# cd evaluator/packages/scaffold/src && uv sync && uv run -m scaffold 