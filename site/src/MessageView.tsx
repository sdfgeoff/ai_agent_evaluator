import type { Message } from './llm_models';


interface MessageTypeData {
  bgClass: string;
  iconSide: 'left' | 'right';
}


const messageTypeData = (message: Message): MessageTypeData => {
  if ('tool_calls' in message) {
    return {
      bgClass: 'bg-tool-request',
      iconSide: 'right',
    }
  } else if ('tool_call_id' in message) {
    return {
      bgClass: 'bg-tool-response',
      iconSide: 'left',
    }
  } else if (message.role === 'user') {
    return {
      bgClass: 'bg-user',
      iconSide: 'left',
    }
  } else {
    return {
      bgClass: 'bg-assistant',
      iconSide: 'right',
    };
  }
}


const Bubble: React.FC<{ children?: React.ReactNode, className: string }> = ({ children, className }) => {
  return <div className={`bubble ${className}`}>
    {children}
  </div>;
}


export const MessageView: React.FC<{ message: Message; }> = ({ message }) => {
  const { bgClass, iconSide } = messageTypeData(message);


  return <div className="d-flex">
    <div>
      <Bubble className={`${iconSide == 'left' ? bgClass : ''} rounded-left padding-1`}>
        {iconSide == 'left' && message.role}
      </Bubble>
    </div>
    <div className={`message padding-1 flex-grow-1 ${bgClass}`}>
      {'tool_calls' in message && (
        <div className="d-flex gap-1 flex-column">
          {message.tool_calls.map((call, index) => (
            <div key={index}>
              <strong>Tool Request: {call.function.name} - {call.id} </strong>
              <div className="pre padding-1">
                {JSON.stringify(call.function.arguments)}
              </div>
            </div>
          ))}
        </div>
      )}
      {'tool_call_id' in message && (
        <div className="tool-call-id">
          <strong>Tool Response: {message.name} - {message.tool_call_id}</strong>
        </div>
      )}
      {'content' in message && (
        <div className="pre padding-1">
          {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
        </div>
      )}
      {'images' in message && message.images && (
        <div className="images">
          {message.images.map((image, index) => (
            <img src={image} alt={`Image ${index + 1}`} key={index} />
          ))}
        </div>
      )}
    </div>
    <div>
      <Bubble className={`${iconSide == 'right' ? bgClass : ''} rounded-right padding-1`}>
        {iconSide == 'right' && message.role}
      </Bubble>
    </div>
  </div>;
};
