import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route, Navigate, Link } from "react-router-dom";
import {
  Box,
  Container,
  Flex,
  HStack,
  Button,
  Spacer,
  Heading,
} from "@chakra-ui/react";
import Protected from "./components/Protected";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Categories from "./pages/Categories";
import UploadReceipt from "./pages/UploadReceipt";
import UploadPdf from "./pages/UploadPdf";

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
        <HStack as="ul" listStyleType="none" gap="4">
          <li>
            <Link to="/">Dashboard</Link>
          </li>
          <li>
            <Link to="/transactions">Transactions</Link>
          </li>
          <li>
            <Link to="/categories">Categories</Link>
          </li>
          <li>
            <Link to="/uploads/receipt">Receipt</Link>
          </li>
          <li>
            <Link to="/uploads/pdf">PDF Import</Link>
          </li>
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
