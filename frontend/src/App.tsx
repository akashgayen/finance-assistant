import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route, Navigate, NavLink } from "react-router-dom";
import Protected from "./components/Protected";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Categories from "./pages/Categories";
import UploadReceipt from "./pages/UploadReceipt";
import UploadPdf from "./pages/UploadPdf";
import { Box } from "@chakra-ui/react/box";
import { Flex } from "@chakra-ui/react/flex";
import { Heading } from "@chakra-ui/react/heading";
import { HStack } from "@chakra-ui/react/stack";
import { Link as ChakraLink } from "@chakra-ui/react/link";
import { Button } from "@chakra-ui/react/button";
import { Spacer } from "@chakra-ui/react/spacer";
import { Container } from "@chakra-ui/react/container";

const qc = new QueryClient();

function Shell({ children }: { children: React.ReactNode }) {
  const onLogout = () => {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  };
  return (
    <Box>
      <Flex
        as="nav"
        px="6"
        py="3"
        borderBottom="1px solid"
        borderColor="gray.200"
        align="center"
        gap="4"
      >
        <Heading size="md">Finance Assistant</Heading>
        <HStack
          as="nav"
          gap="3"
          className="nav-links"
        >
          <ChakraLink asChild>
            <NavLink
              to="/"
              end
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              Dashboard
            </NavLink>
          </ChakraLink>

          <ChakraLink asChild>
            <NavLink
              to="/transactions"
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              Transactions
            </NavLink>
          </ChakraLink>

          <ChakraLink asChild>
            <NavLink
              to="/categories"
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              Categories
            </NavLink>
          </ChakraLink>

          <ChakraLink asChild>
            <NavLink
              to="/uploads/receipt"
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              Receipt
            </NavLink>
          </ChakraLink>

          <ChakraLink asChild>
            <NavLink
              to="/uploads/pdf"
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              PDF Import
            </NavLink>
          </ChakraLink>
        </HStack>
        <Spacer />
        <Button size="sm" onClick={onLogout}>
          Logout
        </Button>
      </Flex>
      <Container maxW="6xl" py="6">
        {children}
      </Container>
    </Box>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        <Route element={<Protected />}>
          <Route
            path="/"
            element={
              <Shell>
                <Dashboard />
              </Shell>
            }
          />
          <Route
            path="/transactions"
            element={
              <Shell>
                <Transactions />
              </Shell>
            }
          />
          <Route
            path="/categories"
            element={
              <Shell>
                <Categories />
              </Shell>
            }
          />
          <Route
            path="/uploads/receipt"
            element={
              <Shell>
                <UploadReceipt />
              </Shell>
            }
          />
          <Route
            path="/uploads/pdf"
            element={
              <Shell>
                <UploadPdf />
              </Shell>
            }
          />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </QueryClientProvider>
  );
}
