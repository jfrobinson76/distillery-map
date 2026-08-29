import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const host = request.headers.get("host");
  if (host === "www.distillerymap.org") {
    const url = request.nextUrl.clone();
    url.host = "distillerymap.org";
    return NextResponse.redirect(url, 308);
  }
}

export const config = {
  matcher: "/:path*",
};
