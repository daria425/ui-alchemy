import { Button } from "@radix-ui/themes";
import { useNavigate } from "react-router";
export default function Main() {
  const nav = useNavigate();
  const handleNavigateToNewChat = () => {
    nav("/app/chat");
  };
  return (
    <div>
      <Button onClick={handleNavigateToNewChat}>New Component</Button>
    </div>
  );
}
