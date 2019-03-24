### Script flags and modificators:  
1. Merging all files into one:  
	* _**Mode:**_  
		* `-m mrg_files` - merging mode.  
	* _**Input:**_  
		* `-if one.txt` - first file for merging;  
		* `-im two.txt` - second file for merging.  
	* _**Result:**_  
		* `-of result.txt` - resulting file.  
	* _**Modificators:**_  
		* `-abc` - sorting strings alphabetically.  
2. Importing with RE:  
	* _**Mode:**_  
		* `-m re_import` - importing with regular expression mode.  
	* _**Input:**_  
		* `-if source.txt` - file for importing.  
	* _**Result:**_  
		* `-of included.txt` - output file with included records;  
		* `-ef excluded.txt` - output file with excluded records.  
	* _**Modificators:**_  
		* `-abc` - sorting strings alphabetically;  
		* `-d domain.com` - domain special value. When this flag absent all records are checking for format errors. If flag is present, then records must contain selected domain in domain part of e-mail address; format errors checking is also available, but very basic.  
3. "Top-X" reports generating:  
	* _**Mode:**_ `-m top_rep` - reports generating mode.  
	* _**Input:**_ `-if input.txt` - file with records to analyse.  
	* _**Result:**_ `-of report.txt` - file with report.  
	* _**Modificators:**_  
		* `-n X` - number of records from top. **Default value** is **`10`**;  
		* `-g Y` – sybdmains count after main domain (level of granularity). **Default value** is **`4`**.  

4. Getting unique addresses:  
	* _**Mode:**_ `-m uniq_addr` - unique addresses filtering.  
	* _**Input:**_ `-if input.txt` - file with records to filter.  
	* _**Result:**_ `-of report.txt` - file with filtered records.  
	* _**Modificators:**_  
		* `-abc` - sorting strings alphabetically.  

### Best way to process leaked text DB:  
1. **Merge all files into one** file with `mrg_files` mode;  
2. **Import all records with general RE** using `re_import` mode;  
	2.1. _(Optional)_ **Filter aim domains** into different files from file with included records (`re_import` mode with `-d` option);  
3. **Generate top-reports** for each file from previous step with options on your choice (`top_rep` mode);  
4. **Get unique email addresses** for futher processing (`uniq_addr` mode).  