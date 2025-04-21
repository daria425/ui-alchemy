import { Text, TextArea, Box } from "@radix-ui/themes";
import { AIMessage } from "../common/Messages";
import { IconButton } from "@radix-ui/themes";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { useState } from "react";
export default function Chat() {
  const textSize = 4;
  const [componentRequest, setComponentRequest] = useState("");
  const handleInput = (e) => {
    setComponentRequest(e.target.value);
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(componentRequest);
    setComponentRequest("");
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
            value={componentRequest}
            onChange={handleInput}
            required
          />
        </Box>
      </form>
    </div>
  );
}
