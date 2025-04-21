import { Text, TextArea, Box } from "@radix-ui/themes";
import { AIMessage } from "../common/Messages";
import { IconButton } from "@radix-ui/themes";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { useState } from "react";
import { useParams, useNavigate } from "react-router";
import { apiConfig } from "../../config/api.config";
export default function Chat() {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const textSize = 4;
  const [userInput, setUserInput] = useState("");
  const [fetchError, setFetchError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const isNewSession = !sessionId;

  const handleInput = (e) => {
    setUserInput(e.target.value);
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) {
      return;
    }
    setLoading(true);
    setFetchError(false);
    try {
      let response;
      if (isNewSession) {
        response = await apiConfig.post("ui-alchemy/api/sessions", {
          description: userInput,
        });
      } else {
        response = await apiConfig.post(
          `ui-alchemy/api/sessions/${sessionId}/messages`,
          {
            message: userInput,
          }
        );
      }
      setApiResponse(response.data);
      console.log("Response data:", response.data);
      setUserInput("");
      nav(`/chat/${response.data.session_id}`);
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
      <AIMessage>
        <Text size={textSize} as="p">
          Welcome to UI Alchemy.{" "}
          <Text size={textSize} weight={"bold"}>
            I’m Alloy.
          </Text>
        </Text>
        <Text size={textSize} as="p">
          Your AI partner in crafting beautiful React components.
        </Text>
        <Text size={textSize} as="p">
          What shall we build today?
        </Text>
      </AIMessage>
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
