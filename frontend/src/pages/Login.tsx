import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  Stack,
  Heading,
  Input,
  Button,
  Text,
} from "@chakra-ui/react";
import { chakra } from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";

const RouterChakraLink = chakra(RouterLink);

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const mut = useMutation({
    mutationFn: async () =>
      (await api.post("/auth/login", { email, password })).data,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      window.location.href = "/";
    },
    onError: () => setErr("Invalid credentials"),
  });
  return (
    <Stack maxW="sm" mx="auto" mt="24" gap="4">
      <Heading size="md">Sign in</Heading>
      {err && <Text color="red.500">{err}</Text>}
      <Input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button
        colorScheme="blue"
        onClick={() => mut.mutate()}
        loading={mut.isPending}
      >
        Login
      </Button>
      <Text>
        New here?{" "}
        <RouterChakraLink to="/signup" color="blue.500">
          Create account
        </RouterChakraLink>
      </Text>
    </Stack>
  );
}
