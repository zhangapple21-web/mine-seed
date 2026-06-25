/**
 * Placeholder Worker — ensures Cloudflare Workers Builds passes
 * regardless of branch content. Real Workers code lives elsewhere.
 */
export default {
  async fetch(_request: Request): Promise<Response> {
    return new Response("mine-seed placeholder — OK", { status: 200 });
  },
} satisfies ExportedHandler;
