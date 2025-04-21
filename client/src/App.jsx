import { RouterProvider, createBrowserRouter } from "react-router";
import RadixTheme from "./config/RadixTheme";
import Index from "./components/common/Index";
import Chat from "./components/chats/Chat";

const router = createBrowserRouter([
  { path: "/", element: <Index /> },
  { path: "/chat", element: <Chat /> },
  { path: "chat/:session_id", element: <Chat /> },
]);

function App() {
  return (
    <RadixTheme>
      <RouterProvider router={router} />
    </RadixTheme>
  );
}

export default App;
