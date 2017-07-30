#include <iostream>
#include "lua.hpp"

int main() {
  lua_State* L = luaL_newstate();
  luaL_openlibs(L);
  int status = luaL_dostring(L, "print('hello lua')");
  return status;
}
