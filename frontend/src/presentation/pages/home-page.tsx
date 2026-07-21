export function HomePage(): React.JSX.Element {
  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="text-3xl font-semibold tracking-tight">Ekko Voice Assistant</h1>
      <p className="mt-3 text-muted-foreground">
        Local assistant runtime is active. Use GraphQL and transcript workflows from the backend
        services.
      </p>
    </main>
  );
}
