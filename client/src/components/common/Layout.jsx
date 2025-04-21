import AppContainer from "./AppContainer";
import { useOutletContext, Outlet } from "react-router";
export default function Layout() {
  const { authenticatedUser } = useOutletContext();
  return (
    <AppContainer>
      <Outlet context={{ authenticatedUser }} />
    </AppContainer>
  );
}
