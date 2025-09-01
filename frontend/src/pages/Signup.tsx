import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  Stack,
  Heading,
  Input,
  Button,
  Text,
  chakra,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";

const RouterChakraLink = chakra(RouterLink);

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const mut = useMutation({
    mutationFn: async () =>
      (await api.post("/auth/signup", { email, password })).data,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      window.location.href = "/";
    },
    onError: () => setErr("Could not create account"),
  });
  return (
    <Stack maxW="sm" mx="auto" mt="24" gap="4">
      <Heading size="md">Create account</Heading>
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
        Sign up
      </Button>
      <Text>
        Have an account?{" "}
        <RouterChakraLink to="/signup" color="blue.500">
          Create account
        </RouterChakraLink>
      </Text>
    </Stack>
  );
}
