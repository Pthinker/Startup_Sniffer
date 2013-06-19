select count(*) from cb_companies where founded_year is not null and category='mobile';

select count(*) from cb_companies join acquisitions on companies.crunch_id=acquisitions.company where companies.category='mobile' and companies.founded_year<2009;


