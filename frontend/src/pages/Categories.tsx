import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  Stack,
  HStack,
  Input,
  Button,
  List,
  ListItem,
  Text,
} from "@chakra-ui/react";

export default function Categories() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const list = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get("/categories")).data,
  });
  const create = useMutation({
    mutationFn: async () => (await api.post("/categories", { name })).data,
    onSuccess: () => {
      setName("");
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });
  return (
    <Stack gap="4">
      <HStack>
        <Input
          placeholder="New category name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Button
          colorScheme="blue"
          onClick={() => create.mutate()}
          loading={create.isPending}
          disabled={!name.trim()}
        >
          Add
        </Button>
      </HStack>
      {list.isError && <Text color="red.500">Failed to load categories</Text>}
      <List.Root gap="2">
        {list.data?.map((c: any) => (
          <ListItem key={c.id}>• {c.name}</ListItem>
        ))}
      </List.Root>
    </Stack>
  );
}
