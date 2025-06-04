export enum Role {
    User = "user",
    Assistant = "assistant",
    Tool = "tool",
}

export enum ToolFunctionType {
    Function = "function",
}

export interface ToolFunctionCall {
    name: string;
    arguments: string;
}

export interface ToolCall {
    id: string;
    type: ToolFunctionType;
    function: ToolFunctionCall;
}

export interface TextMessage {
    role: "user" | "assistant";
    content: string;
    images?: string[];
}

export interface ToolRequestMessage {
    role: "assistant";
    tool_calls: ToolCall[];
}

export interface ToolResponseMessage {
    tool_call_id: string;
    role: "tool";
    name: string;
    content: any; // Use `any` for dynamic content types
}

export interface ToolFunction {
    name: string;
    description?: string;
    parameters: Record<string, any>;
}

export interface ToolDefinition {
    type: ToolFunctionType;
    function: ToolFunction;
}

export type Message = TextMessage | ToolRequestMessage | ToolResponseMessage;
