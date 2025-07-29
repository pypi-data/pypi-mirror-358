/*
 * File:  Options.hh
 * Author:  mikolas
 * Created on:  Fri Nov 18 14:06:04 CAST 2011
 * Copyright (C) 2011, Mikolas Janota
 */
#ifndef OPTIONS_HH_13286
#define OPTIONS_HH_13286
#include <string>
using std::string;
class Options {
public:
  Options();
  bool parse(int count,char** arguments);
  int     verbose;
  string  file_name;
  int     incremental;
  int     qube_input;
  int     test;
  int     unit;
  int     hybrid;
  int     blocking;
  int     pure;
  int     universal_reduction;
  int     help;
private:
};
#endif /* OPTIONS_HH_13286 */
