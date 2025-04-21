import { RouterProvider, createBrowserRouter } from "react-router";
import RadixTheme from "./config/RadixTheme";
import Index from "./components/common/Index";
import Login from "./components/login/Login";
import Chat from "./components/chats/Chat";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Layout from "./components/common/Layout";
import { AuthProvider } from "./contexts/AuthContext";
const router = createBrowserRouter([
  { path: "/", element: <Index /> },
  { path: "/login", element: <Login /> },
  { path: "/403", element: <h1>403</h1> },
  {
    path: "/app",
    element: <ProtectedRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          {
            path: "",
            element: <div>Welcome 2 the app this is a placeholder</div>,
          },
          { path: "chat", element: <Chat /> },
          { path: "chat/sessionId", element: <Chat /> },
        ],
      },
    ],
  },
]);

function App() {
  return (
    <AuthProvider>
      <RadixTheme>
        <RouterProvider router={router} />
      </RadixTheme>
    </AuthProvider>
  );
}

export default App;
