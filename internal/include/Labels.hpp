#include <cstdlib>
#include <json/json.h>

#include "Debug.hpp"

using namespace Json;
using namespace std;

class Labels{
    //Make it singleton: node made for possible several instantiation
    private:
        static constexpr unsigned int STRING_LABEL_ARRAY_SIZE = 50;
        unsigned int  labels_counter[STRING_LABEL_ARRAY_SIZE];
        static string labels_string[STRING_LABEL_ARRAY_SIZE];
        static bool   labels_activated[STRING_LABEL_ARRAY_SIZE];
        static unsigned int current_size;
        // Private Functions
        bool containsLabel(string label);
        int addLabel(string label);
        Debug debug;
    public:
        Labels();
        void displayArrays();
        int update();
        Value getJsonValue();
        int setInRegion(string label);
        int unSetInRegion(string label);
        int setInRegion(const char * label);
        int unSetInRegion(const char * label);
};

