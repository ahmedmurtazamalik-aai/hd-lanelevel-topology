// src/osm_reader.cpp

#include <osmium/io/any_input.hpp>
#include <osmium/handler.hpp>
#include <osmium/visitor.hpp>
#include <osmium/tags/filter.hpp>
#include <osmium/index/map/sparse_mem_array.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>

#include <iostream>
#include <fstream>
#include <unordered_set>

class HighwayHandler : public osmium::handler::Handler
{
public:
    HighwayHandler(std::ofstream &out) : out_csv(out)
    {
        allowed_highway_types = {
            "motorway", "trunk", "primary", "secondary", "tertiary",
            "residential", "living_street", "service"};
    }

    void way(const osmium::Way &way)
    {
        if (!way.tags().has_key("highway"))
            return;

        std::string highway_type = way.tags()["highway"];

        if (allowed_highway_types.find(highway_type) == allowed_highway_types.end())
            return; // Skip undesired highway types

        std::string name = way.tags().has_key("name") ? way.tags()["name"] : "";

        int idx = 0;
        for (const auto &node : way.nodes())
        {
            if (!node.location())
                continue;

            out_csv << way.id() << ","
                    << highway_type << ","
                    << name << ","
                    << idx++ << ","
                    << node.location().lon() << ","
                    << node.location().lat() << "\n";
        }

        std::cout << "Way ID: " << way.id()
                  << ", Type: " << highway_type
                  << ", Name: " << name
                  << ", Nodes: " << way.nodes().size() << std::endl;
    }

private:
    std::ofstream &out_csv;
    std::unordered_set<std::string> allowed_highway_types;
};

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        std::cerr << "Usage: ./osm_reader <file.osm.pbf>" << std::endl;
        return 1;
    }

    std::ofstream out_csv("../data/roads.csv");
    out_csv << "way_id,highway_type,way_name,node_index,lon,lat\n";

    osmium::io::Reader reader(argv[1]);

    using index_type = osmium::index::map::SparseMemArray<osmium::unsigned_object_id_type, osmium::Location>;
    using location_handler_type = osmium::handler::NodeLocationsForWays<index_type>;

    index_type index;
    location_handler_type location_handler(index);

    HighwayHandler handler(out_csv);

    osmium::apply(reader, location_handler, handler);
    reader.close();
    out_csv.close();

    std::cout << "CSV export complete.\n";
    return 0;
}
