import { Text, TextArea } from "@radix-ui/themes";
export default function Chat() {
  const textSize = 4;
  return (
    <div>
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

      <TextArea placeholder="Describe your component here..." />
    </div>
  );
}
