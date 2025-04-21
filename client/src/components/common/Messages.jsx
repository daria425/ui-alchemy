import { Flex, Box } from "@radix-ui/themes";
import uiAlchemyLogo from "../../assets/ui_alchemy.svg";
function AIMessage({ children }) {
  return (
    <Flex align={"start"} gap="1" p="2">
      <img src={uiAlchemyLogo} alt="UI Alchemy Logo" width={50} />
      <Box>{children}</Box>
    </Flex>
  );
}
export { AIMessage };
