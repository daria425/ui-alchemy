import { Theme } from "@radix-ui/themes";

export default function RadixTheme({ children }) {
  return (
    <Theme accentColor="sky" grayColor="mauve" appearance="dark">
      {children}
    </Theme>
  );
}
