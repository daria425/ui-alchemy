import { Text, TextArea, Box, ScrollArea } from "@radix-ui/themes";
import { AIMessage, UserMessage } from "../common/Messages";
import { IconButton } from "@radix-ui/themes";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { useState } from "react";
import { useParams, useNavigate, useOutletContext } from "react-router";
import { apiConfig } from "../../config/api.config";
import { mockMessages } from "../../mocks/mockMessages";
export default function Chat() {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const textSize = 4;
  const [userInput, setUserInput] = useState("");
  const [conversationMessages, setConversationMessages] =
    useState(mockMessages);
  const [fetchError, setFetchError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const isNewSession = !sessionId;
  const { getIdToken } = useOutletContext();
  const handleInput = (e) => {
    setUserInput(e.target.value);
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) {
      return;
    }
    const userMessage = { role: "user", content: userInput };
    setConversationMessages((prev) => [...prev, userMessage]);
    setUserInput("");
    setLoading(true);
    setFetchError(false);
    try {
      let response;
      const idToken = await getIdToken();
      if (isNewSession) {
        response = await apiConfig.post(
          "ui-alchemy/api/sessions",
          {
            description: userInput,
          },
          {
            headers: {
              Authorization: `Bearer ${idToken}`,
            },
          }
        );
        if (response.data.messages && response.data.messages.length > 0) {
          setConversationMessages(response.data.messages);
        }
      } else {
        response = await apiConfig.post(
          `ui-alchemy/api/sessions/${sessionId}/messages`,
          {
            message: userInput,
          },
          {
            headers: {
              Authorization: `Bearer ${idToken}`,
            },
          }
        );
        if (response.data.messages && response.data.messages.length > 0) {
          // Append only the AI message since we already added the user message
          const aiMessage = response.data.messages.filter(
            (msg) => msg.role === "assistant"
          );
          const lastAiMessage = aiMessage[aiMessage.length - 1];
          if (lastAiMessage) {
            setConversationMessages((prev) => [...prev, lastAiMessage]);
          }
        }
      }
      setApiResponse(response.data);
      console.log("Response data:", response.data);
      nav(`/app/chat/${response.data.session_id}`);
    } catch (error) {
      console.error("Error submitting request:", error);
      setFetchError(true);
      if (error.response) {
        console.error("Server error:", error.response.data);
      } else if (error.request) {
        console.error("Network error - no response received");
      } else {
        console.error("Error setting up request:", error.message);
      }
    } finally {
      setLoading(false);
    }
  };
  return (
    <div>
      <ScrollArea
        style={{ height: "calc(100vh - 200px)" }}
        scrollbars="vertical"
      >
        {conversationMessages.map((msg, idx) => {
          if (msg.role === "user") {
            return (
              <UserMessage key={idx}>
                <Text size={textSize}>{msg.content}</Text>
              </UserMessage>
            );
          } else {
            return (
              <div key={idx}>
                <AIMessage>
                  <Text size={textSize}>{msg.content}</Text>
                </AIMessage>
              </div>
            );
          }
        })}
      </ScrollArea>
      <form onSubmit={handleSubmit}>
        <Box position={"relative"}>
          <IconButton
            type="submit"
            style={{
              position: "absolute",
              bottom: "8px",
              right: "8px",
              zIndex: 2,
            }}
          >
            <PaperPlaneIcon />
          </IconButton>
          <TextArea
            placeholder="Describe your component here..."
            style={{ paddingRight: "40px" }}
            value={userInput}
            onChange={handleInput}
            required
          />
        </Box>
      </form>
    </div>
  );
}
