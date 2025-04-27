import { Flex, Box } from "@radix-ui/themes";
import uiAlchemyLogo from "../../assets/ui_alchemy.svg";
import userIcon from "../../assets/userIcon.svg";
function AIMessage({ children }) {
  return (
    <Flex align={"start"} gap="1" p="2" maxWidth={"50%"}>
      <img src={uiAlchemyLogo} alt="UI Alchemy Logo" width={50} />
      <Box>{children}</Box>
    </Flex>
  );
}

function UserMessage({ children }) {
  return (
    <Flex
      align={"start"}
      justify={"end"}
      gap="1"
      p="2"
      maxWidth={"50%"}
      ml="auto"
    >
      <Box>{children}</Box>
      <img src={userIcon} alt="User Icon" width={25} height={25} />
    </Flex>
  );
}
export { AIMessage, UserMessage };
